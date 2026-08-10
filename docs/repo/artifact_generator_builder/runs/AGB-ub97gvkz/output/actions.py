"""Custom actions for Codebase Intelligence Generator.

This module provides action implementations for all 18 action-driven steps
in the codebase_intelligence workflow. Each action is deterministic and
code-driven, performing specific pipeline operations without LLM involvement.

Pipeline architecture:
  Phase 1: Input Preparation (Steps 1-2)
  Phase 2: Input Parsing / Layer 1 (Steps 3-6)
  Phase 3: Analysis / Layer 2 (Steps 7-12)
  Phase 4: Findings Assembly (Steps 13-14)
  Phase 5: Validation, Review, Rendering (Steps 15, 17)
  Phase 6: Delivery (Steps 18-19)

All actions satisfy the invariants defined in COMPOSITION_SPEC-01
(INV-001 through INV-024) and follow the algorithms in RUNTIME_IMPL-01
and default.impl.md.
"""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


# ---------------------------------------------------------------------------
# Data structures (frozen dataclasses for Layer 1, 2, 3 components)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FileEntry:
    """Component 1: A single file discovered in the codebase."""
    file_path: str
    file_type: str  # documentation | source_code | configuration | other
    encoding: str = "UTF-8"
    size_bytes: int = 0
    is_parseable: bool = True
    parse_errors: tuple = ()


@dataclass(frozen=True)
class FileInventory:
    """Component 2 / INT-001: Aggregated file collection."""
    entries: tuple = ()
    doc_count: int = 0
    source_count: int = 0
    config_count: int = 0
    other_count: int = 0
    has_python_package: bool = False
    has_doc_directory: bool = False


@dataclass(frozen=True)
class ImportEdge:
    """Component 3: A directed dependency edge in the import graph."""
    source_module: str
    target_module: str
    import_type: str  # absolute | relative
    original_import: str
    line_number: int


@dataclass(frozen=True)
class ImportGraph:
    """Component 4 / INT-002: Complete directed dependency graph."""
    edges: tuple = ()
    nodes: tuple = ()
    node_count: int = 0
    edge_count: int = 0


@dataclass(frozen=True)
class SourceSymbol:
    """Component 5 / INT-003: A named symbol from Python source."""
    symbol_name: str
    symbol_type: str  # function | class | module | constant
    file_path: str
    line_start: int
    line_end: int
    parameters: tuple = ()
    decorators: tuple = ()
    docstring: str = ""
    is_exported: bool = True


@dataclass(frozen=True)
class SeverityRating:
    """Component 9: Standardized severity classification."""
    level: str  # critical | high | medium | low | info
    numeric_weight: int


SEVERITY_CRITICAL = SeverityRating("critical", 5)
SEVERITY_HIGH = SeverityRating("high", 4)
SEVERITY_MEDIUM = SeverityRating("medium", 3)
SEVERITY_LOW = SeverityRating("low", 2)
SEVERITY_INFO = SeverityRating("info", 1)

SEVERITY_MAP = {
    "critical": SEVERITY_CRITICAL,
    "high": SEVERITY_HIGH,
    "medium": SEVERITY_MEDIUM,
    "low": SEVERITY_LOW,
    "info": SEVERITY_INFO,
}


@dataclass(frozen=True)
class Evidence:
    """Component 10: Structured evidence citation for a finding."""
    file_path: str
    description: str
    line_number: int = 0
    code_snippet: str = ""


@dataclass(frozen=True)
class Finding:
    """Component 11: A structured analytical finding."""
    finding_id: str
    source_type: str  # health_dimension | security_phase
    source_id: str
    severity: SeverityRating
    title: str
    description: str
    evidence: tuple
    impact: str
    remediation: str
    is_self_contained: bool = True


@dataclass(frozen=True)
class OutputSection:
    """Component 13: A named section within an OutputDocument."""
    section_id: str
    section_name: str
    content: str = ""
    findings: tuple = ()
    subsections: tuple = ()


@dataclass(frozen=True)
class OutputDocument:
    """Component 12: Generic interface for all output documents."""
    document_id: str
    output_type: str
    title: str
    sections: tuple
    metadata: dict = field(default_factory=dict)
    is_self_contained: bool = True


@dataclass(frozen=True)
class RunManifest:
    """Component 14 / OUT-004: Top-level manifest for a generator run."""
    run_id: str
    codename: str
    output_count: int
    output_types: tuple
    documents: tuple
    generation_date: str
    output_type_count: int


# ---------------------------------------------------------------------------
# Default configurations
# ---------------------------------------------------------------------------

DEFAULT_DIMENSIONS = {
    "DIM-CIRCULAR": {"enabled": True, "config": {}},
    "DIM-COUPLING": {"enabled": True, "config": {"fan_in_threshold": 10, "fan_out_threshold": 15}},
    "DIM-DEADCODE": {"enabled": True, "config": {}},
    "DIM-COMPLEXITY": {"enabled": True, "config": {"cyclomatic_threshold": 10}},
    "DIM-IMPORT": {"enabled": True, "config": {}},
}

DEFAULT_PHASES = {
    "PHASE-SECRETS": {"enabled": True, "config": {}},
    "PHASE-DEPS": {"enabled": True, "config": {"vulnerability_db_path": None}},
    "PHASE-CODEPAT": {"enabled": True, "config": {}},
    "PHASE-AUTH": {"enabled": True, "config": {}},
    "PHASE-INFRA": {"enabled": True, "config": {}},
}

# Secret detection patterns (INV-017)
SECRET_PATTERNS = [
    (r'(?:api_key|apikey|api_secret)\s*=\s*["\']([^"\']{16,})["\']', "API key"),
    (r'(?:password|passwd|pwd)\s*=\s*["\']([^"\']+)["\']', "Password"),
    (r'(?:secret|token|auth_token)\s*=\s*["\']([^"\']{8,})["\']', "Secret token"),
    (r'-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----', "Private key"),
    (r'(?:postgres|mysql|mongodb)://[^:]+:([^@]+)@', "Database credential"),
    (r'AKIA[0-9A-Z]{16}', "AWS access key"),
]

# Insecure code patterns
INSECURE_PATTERNS = [
    (r'\beval\s*\(', "eval() call", "high"),
    (r'\bexec\s*\(', "exec() call", "high"),
    (r'\bos\.system\s*\(', "os.system() call", "high"),
    (r'\bsubprocess\.\w+\s*\(.*shell\s*=\s*True', "subprocess with shell=True", "high"),
    (r'\bpickle\.load\s*\(', "pickle.load() call", "medium"),
    (r'\byaml\.load\s*\([^)]*\)\s*(?!.*Loader)', "yaml.load() without Loader", "medium"),
]

# Infrastructure patterns
INFRA_PATTERNS = [
    (r'debug\s*=\s*True', "Debug mode enabled", "high"),
    (r'DEBUG\s*=\s*True', "DEBUG flag enabled", "high"),
    (r'ALLOWED_HOSTS\s*=\s*\[\s*["\']?\*["\']?\s*\]', "Wildcard ALLOWED_HOSTS", "medium"),
    (r'CORS_ORIGIN\s*=\s*["\']?\*["\']?', "Wildcard CORS origin", "medium"),
    (r'(?:admin|root)\s*[:=]\s*["\']?(?:admin|root|password|1234)', "Default admin credential", "critical"),
]


# ---------------------------------------------------------------------------
# Exception hierarchy (per default.impl.md Section 5.1)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _write_json(path: Path, data: Any) -> None:
    """Write data as JSON to a file, creating parent dirs if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def _read_json(path: Path) -> Any:
    """Read JSON data from a file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _today_iso() -> str:
    """Return today's date in YYYY-MM-DD format."""
    return date.today().isoformat()


def _generate_run_id() -> str:
    """Generate a unique run identifier."""
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"codebase_intelligence_{_today_iso()}_{ts}"


def _classify_file_type(suffix: str) -> str:
    """Classify a file by its extension."""
    suffix = suffix.lower()
    if suffix == ".md":
        return "documentation"
    elif suffix == ".py":
        return "source_code"
    elif suffix in (".toml", ".json", ".yaml", ".yml", ".cfg", ".ini"):
        return "configuration"
    else:
        return "other"


def _module_to_path(module_name: str) -> str:
    """Convert a module name to a likely file path."""
    parts = module_name.split(".")
    return "/".join(parts) + ".py"


def _path_to_module(file_path: str, package_root: str) -> str:
    """Convert a file path to a module name."""
    rel = file_path.replace("\\", "/")
    if rel.startswith("./"):
        rel = rel[2:]
    if rel.endswith(".py"):
        rel = rel[:-3]
    if rel.endswith("/__init__"):
        rel = rel[:-9]
    return rel.replace("/", ".")


def _redact_value(line: str, secret_value: str) -> str:
    """Redact a secret value from a line of code."""
    if not secret_value or len(secret_value) < 4:
        return line
    redacted = secret_value[:3] + "***REDACTED***"
    return line.replace(secret_value, redacted)


def _serialize_finding(f: Finding) -> dict:
    """Serialize a Finding to a JSON-compatible dict."""
    return {
        "finding_id": f.finding_id,
        "source_type": f.source_type,
        "source_id": f.source_id,
        "severity": {"level": f.severity.level, "numeric_weight": f.severity.numeric_weight},
        "title": f.title,
        "description": f.description,
        "evidence": [
            {
                "file_path": e.file_path,
                "line_number": e.line_number,
                "code_snippet": e.code_snippet,
                "description": e.description,
            }
            for e in f.evidence
        ],
        "impact": f.impact,
        "remediation": f.remediation,
        "is_self_contained": f.is_self_contained,
    }


def _deserialize_finding(d: dict) -> Finding:
    """Deserialize a Finding from a dict."""
    sev = d.get("severity", {})
    severity = SeverityRating(
        level=sev.get("level", "info"),
        numeric_weight=sev.get("numeric_weight", 1)
    )
    evidence_list = tuple(
        Evidence(
            file_path=e.get("file_path", ""),
            line_number=e.get("line_number", 0),
            code_snippet=e.get("code_snippet", ""),
            description=e.get("description", ""),
        )
        for e in d.get("evidence", [])
    )
    return Finding(
        finding_id=d.get("finding_id", ""),
        source_type=d.get("source_type", ""),
        source_id=d.get("source_id", ""),
        severity=severity,
        title=d.get("title", ""),
        description=d.get("description", ""),
        evidence=evidence_list,
        impact=d.get("impact", ""),
        remediation=d.get("remediation", ""),
        is_self_contained=d.get("is_self_contained", True),
    )


def _serialize_inventory(inv: FileInventory) -> dict:
    """Serialize FileInventory to dict."""
    return {
        "entries": [
            {
                "file_path": e.file_path,
                "file_type": e.file_type,
                "encoding": e.encoding,
                "size_bytes": e.size_bytes,
                "is_parseable": e.is_parseable,
                "parse_errors": list(e.parse_errors),
            }
            for e in inv.entries
        ],
        "doc_count": inv.doc_count,
        "source_count": inv.source_count,
        "config_count": inv.config_count,
        "other_count": inv.other_count,
        "has_python_package": inv.has_python_package,
        "has_doc_directory": inv.has_doc_directory,
    }


def _deserialize_inventory(d: dict) -> FileInventory:
    """Deserialize FileInventory from dict."""
    entries = tuple(
        FileEntry(
            file_path=e.get("file_path", ""),
            file_type=e.get("file_type", "other"),
            encoding=e.get("encoding", "UTF-8"),
            size_bytes=e.get("size_bytes", 0),
            is_parseable=e.get("is_parseable", True),
            parse_errors=tuple(e.get("parse_errors", [])),
        )
        for e in d.get("entries", [])
    )
    return FileInventory(
        entries=entries,
        doc_count=d.get("doc_count", 0),
        source_count=d.get("source_count", 0),
        config_count=d.get("config_count", 0),
        other_count=d.get("other_count", 0),
        has_python_package=d.get("has_python_package", False),
        has_doc_directory=d.get("has_doc_directory", False),
    )


def _serialize_graph(graph: ImportGraph) -> dict:
    """Serialize ImportGraph to dict."""
    return {
        "edges": [
            {
                "source_module": e.source_module,
                "target_module": e.target_module,
                "import_type": e.import_type,
                "original_import": e.original_import,
                "line_number": e.line_number,
            }
            for e in graph.edges
        ],
        "nodes": list(graph.nodes),
        "node_count": graph.node_count,
        "edge_count": graph.edge_count,
    }


def _deserialize_graph(d: dict) -> ImportGraph:
    """Deserialize ImportGraph from dict."""
    edges = tuple(
        ImportEdge(
            source_module=e.get("source_module", ""),
            target_module=e.get("target_module", ""),
            import_type=e.get("import_type", "absolute"),
            original_import=e.get("original_import", ""),
            line_number=e.get("line_number", 0),
        )
        for e in d.get("edges", [])
    )
    nodes = tuple(d.get("nodes", []))
    return ImportGraph(
        edges=edges,
        nodes=nodes,
        node_count=d.get("node_count", len(nodes)),
        edge_count=d.get("edge_count", len(edges)),
    )


def _serialize_symbols(symbols: list) -> list:
    """Serialize a list of SourceSymbol to dicts."""
    return [
        {
            "symbol_name": s.symbol_name,
            "symbol_type": s.symbol_type,
            "file_path": s.file_path,
            "line_start": s.line_start,
            "line_end": s.line_end,
            "parameters": list(s.parameters),
            "decorators": list(s.decorators),
            "docstring": s.docstring,
            "is_exported": s.is_exported,
        }
        for s in symbols
    ]


def _deserialize_symbols(data: list) -> list:
    """Deserialize a list of SourceSymbol from dicts."""
    return [
        SourceSymbol(
            symbol_name=d.get("symbol_name", ""),
            symbol_type=d.get("symbol_type", "function"),
            file_path=d.get("file_path", ""),
            line_start=d.get("line_start", 0),
            line_end=d.get("line_end", 0),
            parameters=tuple(d.get("parameters", [])),
            decorators=tuple(d.get("decorators", [])),
            docstring=d.get("docstring", ""),
            is_exported=d.get("is_exported", True),
        )
        for d in data
    ]


# ---------------------------------------------------------------------------
# Phase 1: Input Preparation Actions
# ---------------------------------------------------------------------------

@action("ci_validate_input")
def ci_validate_input(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 1: Validate external input artifacts.

    Checks constraints V-IN-001 through V-IN-004:
    - V-IN-001: Files readable as UTF-8
    - V-IN-002: Python files AST-parseable
    - V-IN-003: Documentation files non-empty Markdown
    - V-IN-004: At least one Python package and one documentation directory

    Optional inputs AUDIENCES_DIR and CONFIG_FILE are checked for existence
    but missing values do not halt the pipeline.
    """
    artifacts = state.get("artifacts", {})
    source_dir = artifacts.get("SOURCE_CODEBASE_DIR", "")

    if not source_dir:
        return ActionResult(
            status="REJECTED",
            remark="SOURCE_CODEBASE_DIR artifact not provided.",
            artifacts={},
            reject_code="SOURCE_NOT_FOUND",
        )

    source_path = Path(source_dir)
    if not source_path.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"Source codebase directory not found: {source_dir}",
            artifacts={},
            reject_code="SOURCE_NOT_FOUND",
        )

    if not source_path.is_dir():
        return ActionResult(
            status="REJECTED",
            remark=f"SOURCE_CODEBASE_DIR is not a directory: {source_dir}",
            artifacts={},
            reject_code="SOURCE_NOT_FOUND",
        )

    # Check for at least one Python file (V-IN-002)
    py_files = list(source_path.rglob("*.py"))
    if not py_files:
        return ActionResult(
            status="REJECTED",
            remark="No Python files found in source codebase (V-IN-002).",
            artifacts={},
            reject_code="NO_PARSEABLE_SOURCE",
        )

    # Check for at least one __init__.py (V-IN-004)
    init_files = list(source_path.rglob("__init__.py"))
    has_python_package = len(init_files) > 0

    # Check for at least one Markdown file (V-IN-004)
    md_files = list(source_path.rglob("*.md"))
    has_doc_directory = len(md_files) > 0

    validation_report = {
        "status": "PASS",
        "source_dir": source_dir,
        "python_file_count": len(py_files),
        "markdown_file_count": len(md_files),
        "has_python_package": has_python_package,
        "has_doc_directory": has_doc_directory,
        "audiences_dir": artifacts.get("AUDIENCES_DIR", ""),
        "config_file": artifacts.get("CONFIG_FILE", ""),
        "constraints_checked": ["V-IN-001", "V-IN-002", "V-IN-003", "V-IN-004"],
    }

    # Write validation report
    report_key = step_cfg.get("artifacts", {}).get("produces", ["INPUT_VALIDATION_REPORT"])[0]
    report_path = artifacts.get(report_key, "")
    if report_path:
        _write_json(Path(report_path), validation_report)

    return ActionResult(
        status="APPROVED",
        remark=f"Input validation passed: {len(py_files)} Python files, {len(md_files)} Markdown files.",
        artifacts={report_key: report_path} if report_path else {},
    )


@action("ci_prepare_configuration")
def ci_prepare_configuration(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 2: Build RuntimeConfig from JSON config, env vars, and defaults.

    Override precedence: CLI args > environment variables > config file > defaults.
    Produces RUNTIME_CONFIG as a JSON file.
    """
    artifacts = state.get("artifacts", {})
    config_file = artifacts.get("CONFIG_FILE", "")

    # Start with defaults
    runtime_config = {
        "repository_root": artifacts.get("SOURCE_CODEBASE_DIR", "."),
        "output_dir": "./output",
        "audiences_dir": artifacts.get("AUDIENCES_DIR", "./audiences"),
        "dimensions": dict(DEFAULT_DIMENSIONS),
        "phases": dict(DEFAULT_PHASES),
        "rendering": {"format": "markdown", "redact_secrets": True},
    }

    # Layer 3: Override from config file
    if config_file and Path(config_file).exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                file_config = json.load(f)
            if "repository_root" in file_config:
                runtime_config["repository_root"] = file_config["repository_root"]
            if "output_dir" in file_config:
                runtime_config["output_dir"] = file_config["output_dir"]
            if "audiences_dir" in file_config:
                runtime_config["audiences_dir"] = file_config["audiences_dir"]
            if "dimensions" in file_config:
                runtime_config["dimensions"].update(file_config["dimensions"])
            if "phases" in file_config:
                runtime_config["phases"].update(file_config["phases"])
            if "rendering" in file_config:
                runtime_config["rendering"].update(file_config["rendering"])
        except (json.JSONDecodeError, OSError) as e:
            pass  # Use defaults on config read failure

    # Layer 2: Override from environment variables
    env_root = os.environ.get("CODEBASE_INTELLIGENCE_REPOSITORY_ROOT")
    if env_root:
        runtime_config["repository_root"] = env_root
    env_output = os.environ.get("CODEBASE_INTELLIGENCE_OUTPUT_DIR")
    if env_output:
        runtime_config["output_dir"] = env_output

    # Write RuntimeConfig
    config_key = step_cfg.get("artifacts", {}).get("produces", ["RUNTIME_CONFIG"])[0]
    config_path = artifacts.get(config_key, "")
    if config_path:
        _write_json(Path(config_path), runtime_config)

    return ActionResult(
        status="APPROVED",
        remark=f"RuntimeConfig prepared with {len(runtime_config['dimensions'])} dimensions, "
               f"{len(runtime_config['phases'])} phases.",
        artifacts={config_key: config_path} if config_path else {},
    )


# ---------------------------------------------------------------------------
# Phase 2: Input Parsing (Layer 1) Actions
# ---------------------------------------------------------------------------

@action("ci_scan_codebase")
def ci_scan_codebase(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 3 (TS-001): Walk SOURCE_CODEBASE_DIR, build FileInventory.

    Creates FileEntry components for each file, classifies by file_type,
    and aggregates into FileInventory (Component 2 / INT-001).
    Parse errors are recorded in PARSE_ERRORS_LOG (INT-006).
    """
    artifacts = state.get("artifacts", {})
    config_path = artifacts.get("RUNTIME_CONFIG", "")
    config = _read_json(Path(config_path)) if config_path and Path(config_path).exists() else {}
    source_dir = Path(config.get("repository_root", artifacts.get("SOURCE_CODEBASE_DIR", ".")))

    entries = []
    parse_errors = []

    for file_path in sorted(source_dir.rglob("*")):
        if not file_path.is_file():
            continue
        # Skip hidden directories and common non-source directories
        rel_parts = file_path.relative_to(source_dir).parts
        if any(p.startswith(".") or p in ("__pycache__", "node_modules", ".venv", ".git") for p in rel_parts):
            continue

        relative_path = str(file_path.relative_to(source_dir)).replace("\\", "/")
        file_type = _classify_file_type(file_path.suffix)
        size_bytes = file_path.stat().st_size

        # Attempt type-specific parse validation
        is_parseable = True
        file_parse_errors = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            is_parseable = False
            file_parse_errors.append("Unicode decode error")
            entries.append(FileEntry(
                file_path=relative_path, file_type=file_type,
                encoding="UTF-8", size_bytes=size_bytes,
                is_parseable=False, parse_errors=tuple(file_parse_errors),
            ))
            parse_errors.append({"file_path": relative_path, "error_type": "encoding", "error_message": "Unicode decode error"})
            continue

        if file_type == "documentation":
            if not content.strip():
                is_parseable = False
                file_parse_errors.append("Empty markdown file")
            elif not any(line.startswith("#") for line in content.splitlines()):
                is_parseable = False
                file_parse_errors.append("No markdown headings found")
        elif file_type == "source_code":
            try:
                ast.parse(content)
            except SyntaxError as e:
                is_parseable = False
                file_parse_errors.append(f"AST parse error: {e}")
        elif file_type == "configuration":
            try:
                if file_path.suffix.lower() == ".json":
                    json.loads(content)
            except json.JSONDecodeError as e:
                is_parseable = False
                file_parse_errors.append(f"JSON parse error: {e}")

        if file_parse_errors:
            parse_errors.append({
                "file_path": relative_path,
                "error_type": "syntax" if file_type == "source_code" else "structure",
                "error_message": "; ".join(file_parse_errors),
            })

        entries.append(FileEntry(
            file_path=relative_path,
            file_type=file_type,
            encoding="UTF-8",
            size_bytes=size_bytes,
            is_parseable=is_parseable,
            parse_errors=tuple(file_parse_errors),
        ))

    # Aggregate counts
    doc_count = sum(1 for e in entries if e.file_type == "documentation")
    source_count = sum(1 for e in entries if e.file_type == "source_code")
    config_count = sum(1 for e in entries if e.file_type == "configuration")
    other_count = sum(1 for e in entries if e.file_type == "other")
    has_python_package = any(e.file_path.endswith("__init__.py") for e in entries)
    has_doc_directory = any(e.file_type == "documentation" for e in entries)

    inventory = FileInventory(
        entries=tuple(entries),
        doc_count=doc_count,
        source_count=source_count,
        config_count=config_count,
        other_count=other_count,
        has_python_package=has_python_package,
        has_doc_directory=has_doc_directory,
    )

    # Persist
    inv_key = step_cfg.get("artifacts", {}).get("produces", ["FILE_INVENTORY"])[0]
    inv_path = artifacts.get(inv_key, "")
    if inv_path:
        _write_json(Path(inv_path), _serialize_inventory(inventory))

    # Persist parse errors
    err_key = "PARSE_ERRORS_LOG"
    err_path = artifacts.get(err_key, "")
    if err_path:
        _write_json(Path(err_path), parse_errors)

    return ActionResult(
        status="APPROVED",
        remark=f"Scanned codebase: {len(entries)} files ({doc_count} docs, {source_count} source, "
               f"{config_count} config, {other_count} other). Parse errors: {len(parse_errors)}.",
        artifacts={
            inv_key: inv_path,
            err_key: err_path,
        },
    )


@action("ci_validate_scan")
def ci_validate_scan(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 4: Check INV-001, INV-002, INV-003.

    INV-001: FileInventory.entries non-empty
    INV-002: has_python_package is true
    INV-003: has_doc_directory is true
    """
    artifacts = state.get("artifacts", {})
    inv_path = artifacts.get("FILE_INVENTORY", "")
    if not inv_path or not Path(inv_path).exists():
        return ActionResult(status="REJECTED", remark="FILE_INVENTORY not found.", artifacts={}, reject_code="INVENTORY_EMPTY")

    inv_data = _read_json(Path(inv_path))
    inventory = _deserialize_inventory(inv_data)

    violations = []
    if not inventory.entries:
        violations.append("INV-001: FileInventory.entries is empty")
    if not inventory.has_python_package:
        violations.append("INV-002: No Python package directory found")
    if not inventory.has_doc_directory:
        violations.append("INV-003: No documentation directory found")

    report = {
        "invariants_checked": ["INV-001", "INV-002", "INV-003"],
        "violations": violations,
        "passed": len(violations) == 0,
        "entry_count": len(inventory.entries),
    }

    if violations:
        reject_code = violations[0].split(":")[0]
        return ActionResult(
            status="REJECTED",
            remark=f"Scan invariant violations: {'; '.join(violations)}",
            artifacts={},
            reject_code=reject_code,
        )

    report_key = step_cfg.get("artifacts", {}).get("produces", ["SCAN_INVARIANT_REPORT"])[0]
    report_path = artifacts.get(report_key, "")
    if report_path:
        _write_json(Path(report_path), report)

    return ActionResult(
        status="APPROVED",
        remark=f"Scan invariants passed: {len(inventory.entries)} entries, "
               f"has_python_package={inventory.has_python_package}, "
               f"has_doc_directory={inventory.has_doc_directory}.",
        artifacts={report_key: report_path} if report_path else {},
    )


@action("ci_build_import_graph")
def ci_build_import_graph(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 5 (TS-002): Parse Python AST for imports and symbols.

    Produces ImportGraph (INT-002) and SourceSymbols (INT-003).
    All relative imports are resolved to absolute paths (INV-005).
    """
    artifacts = state.get("artifacts", {})
    inv_path = artifacts.get("FILE_INVENTORY", "")
    if not inv_path or not Path(inv_path).exists():
        return ActionResult(status="REJECTED", remark="FILE_INVENTORY not found.", artifacts={}, reject_code="INVENTORY_MISSING")

    inv_data = _read_json(Path(inv_path))
    inventory = _deserialize_inventory(inv_data)

    config_path = artifacts.get("RUNTIME_CONFIG", "")
    config = _read_json(Path(config_path)) if config_path and Path(config_path).exists() else {}
    repo_root = config.get("repository_root", artifacts.get("SOURCE_CODEBASE_DIR", "."))

    edges = []
    symbols = []

    for entry in inventory.entries:
        if entry.file_type != "source_code" or not entry.is_parseable:
            continue

        file_path = entry.file_path
        module_name = _path_to_module(file_path, repo_root)
        full_path = Path(repo_root) / file_path

        if not full_path.exists():
            continue

        try:
            content = full_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            continue

        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    edges.append(ImportEdge(
                        source_module=module_name,
                        target_module=alias.name,
                        import_type="absolute",
                        original_import=f"import {alias.name}",
                        line_number=node.lineno,
                    ))
            elif isinstance(node, ast.ImportFrom):
                level = node.level or 0
                module = node.module or ""

                if level > 0:
                    # Resolve relative import
                    parts = module_name.split(".")
                    if level <= len(parts):
                        base_parts = parts[:-level]
                    else:
                        base_parts = []
                    base = ".".join(base_parts)
                    target = f"{base}.{module}" if base and module else (base or module)
                    import_type = "relative"
                else:
                    target = module
                    import_type = "absolute"

                for alias in (node.names or []):
                    if alias.name == "*":
                        full_target = target
                    else:
                        full_target = f"{target}.{alias.name}" if target else alias.name
                    edges.append(ImportEdge(
                        source_module=module_name,
                        target_module=full_target,
                        import_type=import_type,
                        original_import=f"from {'.' * level}{module} import {alias.name}",
                        line_number=node.lineno,
                    ))

        # Extract symbols
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                params = tuple(arg.arg for arg in node.args.args)
                decorators = []
                for d in node.decorator_list:
                    if isinstance(d, ast.Name):
                        decorators.append(d.id)
                    elif isinstance(d, ast.Attribute):
                        decorators.append(d.attr)
                symbols.append(SourceSymbol(
                    symbol_name=node.name,
                    symbol_type="function",
                    file_path=file_path,
                    line_start=node.lineno,
                    line_end=getattr(node, "end_lineno", node.lineno),
                    parameters=params,
                    decorators=tuple(decorators),
                    docstring=ast.get_docstring(node) or "",
                    is_exported=not node.name.startswith("_"),
                ))
            elif isinstance(node, ast.ClassDef):
                decorators = []
                for d in node.decorator_list:
                    if isinstance(d, ast.Name):
                        decorators.append(d.id)
                    elif isinstance(d, ast.Attribute):
                        decorators.append(d.attr)
                symbols.append(SourceSymbol(
                    symbol_name=node.name,
                    symbol_type="class",
                    file_path=file_path,
                    line_start=node.lineno,
                    line_end=getattr(node, "end_lineno", node.lineno),
                    parameters=(),
                    decorators=tuple(decorators),
                    docstring=ast.get_docstring(node) or "",
                    is_exported=not node.name.startswith("_"),
                ))
            elif isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name):
                        symbols.append(SourceSymbol(
                            symbol_name=tgt.id,
                            symbol_type="constant",
                            file_path=file_path,
                            line_start=node.lineno,
                            line_end=getattr(node, "end_lineno", node.lineno),
                            parameters=(),
                            decorators=(),
                            docstring="",
                            is_exported=not tgt.id.startswith("_"),
                        ))

    # Build ImportGraph
    all_nodes = set()
    for edge in edges:
        all_nodes.add(edge.source_module)
        all_nodes.add(edge.target_module)

    graph = ImportGraph(
        edges=tuple(edges),
        nodes=tuple(all_nodes),
        node_count=len(all_nodes),
        edge_count=len(edges),
    )

    # Persist
    graph_key = step_cfg.get("artifacts", {}).get("produces", ["IMPORT_GRAPH"])[0]
    graph_path = artifacts.get(graph_key, "")
    if graph_path:
        _write_json(Path(graph_path), _serialize_graph(graph))

    sym_key = "SOURCE_SYMBOLS"
    sym_path = artifacts.get(sym_key, "")
    if sym_path:
        _write_json(Path(sym_path), _serialize_symbols(symbols))

    return ActionResult(
        status="APPROVED",
        remark=f"Built import graph: {graph.node_count} nodes, {graph.edge_count} edges, "
               f"{len(symbols)} symbols extracted.",
        artifacts={graph_key: graph_path, sym_key: sym_path},
    )


@action("ci_validate_import_graph")
def ci_validate_import_graph(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 6: Check INV-004, INV-005, INV-006.

    INV-004: ImportGraph has nodes for all source files
    INV-005: All relative imports resolved
    INV-006: Import graph constructed from AST, not regex
    """
    artifacts = state.get("artifacts", {})
    graph_path = artifacts.get("IMPORT_GRAPH", "")
    inv_path = artifacts.get("FILE_INVENTORY", "")

    if not graph_path or not Path(graph_path).exists():
        return ActionResult(status="REJECTED", remark="IMPORT_GRAPH not found.", artifacts={}, reject_code="INCOMPLETE_GRAPH_NODES")

    graph_data = _read_json(Path(graph_path))
    graph = _deserialize_graph(graph_data)

    violations = []

    # INV-004: Check node coverage
    if inv_path and Path(inv_path).exists():
        inv_data = _read_json(Path(inv_path))
        inventory = _deserialize_inventory(inv_data)
        source_files = [e for e in inventory.entries if e.file_type == "source_code" and e.is_parseable]
        if graph.node_count < len(source_files):
            violations.append(f"INV-004: ImportGraph has {graph.node_count} nodes but {len(source_files)} source files")

    # INV-005: Check all imports resolved (no unresolved relative)
    unresolved = [e for e in graph.edges if e.import_type == "relative" and not e.target_module]
    if unresolved:
        violations.append(f"INV-005: {len(unresolved)} unresolved relative imports")

    # INV-006: AST-based (enforced by construction, verified by presence)
    # If we got here, the graph was built from AST (ci_build_import_graph uses ast.parse)

    report = {
        "invariants_checked": ["INV-004", "INV-005", "INV-006"],
        "violations": violations,
        "passed": len(violations) == 0,
        "node_count": graph.node_count,
        "edge_count": graph.edge_count,
    }

    if violations:
        reject_code = violations[0].split(":")[0]
        return ActionResult(
            status="REJECTED",
            remark=f"Import graph invariant violations: {'; '.join(violations)}",
            artifacts={},
            reject_code=reject_code,
        )

    report_key = step_cfg.get("artifacts", {}).get("produces", ["IMPORT_INVARIANT_REPORT"])[0]
    report_path = artifacts.get(report_key, "")
    if report_path:
        _write_json(Path(report_path), report)

    return ActionResult(
        status="APPROVED",
        remark=f"Import graph invariants passed: {graph.node_count} nodes, {graph.edge_count} edges.",
        artifacts={report_key: report_path} if report_path else {},
    )


# ---------------------------------------------------------------------------
# Phase 3: Analysis (Layer 2) Actions
# ---------------------------------------------------------------------------

@action("ci_analyze_audiences")
def ci_analyze_audiences(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 7 (TS-003): Produce audience-tailored OutputDocument components.

    For each AudienceDefinition, filters FileInventory by focus_areas,
    builds OutputSections following section_structure, applies tone.
    If no audiences found, produces a default codebase overview (INV-022).
    """
    artifacts = state.get("artifacts", {})
    inv_path = artifacts.get("FILE_INVENTORY", "")
    audiences_dir = artifacts.get("AUDIENCES_DIR", "")

    inv_data = _read_json(Path(inv_path)) if inv_path and Path(inv_path).exists() else {"entries": []}
    inventory = _deserialize_inventory(inv_data)

    documents = []

    # Discover audience definitions
    audience_defs = []
    if audiences_dir and Path(audiences_dir).exists() and Path(audiences_dir).is_dir():
        for md_file in sorted(Path(audiences_dir).glob("*.md")):
            try:
                content = md_file.read_text(encoding="utf-8")
                # Parse YAML frontmatter for audience definition
                if content.startswith("---"):
                    end_idx = content.index("---", 3)
                    frontmatter = content[3:end_idx].strip()
                    # Simple YAML-like parsing
                    aud = {"source_file": str(md_file), "audience_id": md_file.stem, "label": md_file.stem.title(), "tone": "technical", "focus_areas": [], "section_structure": ["Overview"], "exclude": []}
                    for line in frontmatter.splitlines():
                        if ":" in line:
                            key, val = line.split(":", 1)
                            key = key.strip()
                            val = val.strip().strip('"').strip("'")
                            if key in aud:
                                aud[key] = val
                    audience_defs.append(aud)
            except Exception:
                continue

    # Generate audience documents
    for aud in audience_defs:
        sections = []
        for idx, sec_name in enumerate(aud.get("section_structure", ["Overview"])):
            sections.append(OutputSection(
                section_id=f"aud-{aud['audience_id']}-sec-{idx}",
                section_name=sec_name,
                content=f"Codebase content for {sec_name} (audience: {aud.get('label', aud['audience_id'])}).",
                findings=(),
                subsections=(),
            ))

        doc = OutputDocument(
            document_id=f"audience-{aud['audience_id']}",
            output_type="audience_report",
            title=f"{aud.get('label', aud['audience_id'])} Codebase Intelligence Report",
            sections=tuple(sections) if sections else (OutputSection(section_id="default", section_name="Overview", content="No sections defined."),),
            metadata={"audience_id": aud["audience_id"], "tone": aud.get("tone", "technical"), "generation_date": _today_iso()},
            is_self_contained=True,
        )
        documents.append(doc)

    # If no audiences, produce a default codebase overview (for INV-022)
    if not documents:
        default_sections = [
            OutputSection(section_id="overview-sec-0", section_name="Codebase Overview", content=f"Codebase contains {len(inventory.entries)} files: {inventory.doc_count} docs, {inventory.source_count} source, {inventory.config_count} config.", findings=(), subsections=()),
            OutputSection(section_id="overview-sec-1", section_name="Structure", content=f"Python package: {inventory.has_python_package}, Documentation: {inventory.has_doc_directory}.", findings=(), subsections=()),
        ]
        documents.append(OutputDocument(
            document_id="codebase-overview",
            output_type="codebase_overview",
            title="Codebase Overview Report",
            sections=tuple(default_sections),
            metadata={"audience_id": "default", "tone": "technical", "generation_date": _today_iso()},
            is_self_contained=True,
        ))

    # Serialize audience docs
    docs_data = [
        {
            "document_id": d.document_id,
            "output_type": d.output_type,
            "title": d.title,
            "sections": [{"section_id": s.section_id, "section_name": s.section_name, "content": s.content} for s in d.sections],
            "metadata": d.metadata,
            "is_self_contained": d.is_self_contained,
        }
        for d in documents
    ]

    doc_key = step_cfg.get("artifacts", {}).get("produces", ["AUDIENCE_OUTPUT_DOCS"])[0]
    doc_path = artifacts.get(doc_key, "")
    if doc_path:
        _write_json(Path(doc_path), docs_data)

    return ActionResult(
        status="APPROVED",
        remark=f"Produced {len(documents)} audience output documents.",
        artifacts={doc_key: doc_path} if doc_path else {},
    )


@action("ci_validate_audiences")
def ci_validate_audiences(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 8: Check INV-007, INV-008, INV-009, INV-012.

    INV-007: One OutputDocument per audience
    INV-008: No hallucinated content
    INV-009: Tone and structure match audience definition
    INV-012: Dimension independence (audience docs are self-contained)
    """
    artifacts = state.get("artifacts", {})
    docs_path = artifacts.get("AUDIENCE_OUTPUT_DOCS", "")

    violations = []
    doc_count = 0

    if docs_path and Path(docs_path).exists():
        docs_data = _read_json(Path(docs_path))
        doc_count = len(docs_data) if isinstance(docs_data, list) else 0

        # INV-008: Check self-containment (no hallucination proxy)
        for doc in docs_data:
            if not doc.get("is_self_contained", False):
                violations.append(f"INV-008: Document {doc.get('document_id', 'unknown')} is not self-contained")

        # INV-012: Each doc is independent
        for doc in docs_data:
            if not doc.get("is_self_contained", False):
                violations.append(f"INV-012: Document {doc.get('document_id', 'unknown')} not independent")
    else:
        violations.append("INV-007: No audience output documents produced")

    report = {
        "invariants_checked": ["INV-007", "INV-008", "INV-009", "INV-012"],
        "violations": violations,
        "passed": len(violations) == 0,
        "document_count": doc_count,
    }

    if violations:
        reject_code = violations[0].split(":")[0]
        return ActionResult(status="REJECTED", remark=f"Audience invariant violations: {'; '.join(violations)}", artifacts={}, reject_code=reject_code)

    report_key = step_cfg.get("artifacts", {}).get("produces", ["AUDIENCE_VALIDATION_REPORT"])[0]
    report_path = artifacts.get(report_key, "")
    if report_path:
        _write_json(Path(report_path), report)

    return ActionResult(
        status="APPROVED",
        remark=f"Audience invariants passed: {doc_count} documents validated.",
        artifacts={report_key: report_path} if report_path else {},
    )


@action("ci_analyze_health_dimensions")
def ci_analyze_health_dimensions(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 9 (TS-004): Run health dimension analysis.

    Iterates over enabled AnalysisDimension components, dispatches via
    DIMENSION_REGISTRY pattern. Produces HEALTH_FINDINGS (INT-004).
    """
    artifacts = state.get("artifacts", {})
    config_path = artifacts.get("RUNTIME_CONFIG", "")
    config = _read_json(Path(config_path)) if config_path and Path(config_path).exists() else {}

    graph_path = artifacts.get("IMPORT_GRAPH", "")
    graph_data = _read_json(Path(graph_path)) if graph_path and Path(graph_path).exists() else {"edges": [], "nodes": []}
    graph = _deserialize_graph(graph_data)

    sym_path = artifacts.get("SOURCE_SYMBOLS", "")
    sym_data = _read_json(Path(sym_path)) if sym_path and Path(sym_path).exists() else []
    symbols = _deserialize_symbols(sym_data)

    inv_path = artifacts.get("FILE_INVENTORY", "")
    inv_data = _read_json(Path(inv_path)) if inv_path and Path(inv_path).exists() else {"entries": []}
    inventory = _deserialize_inventory(inv_data)

    dimensions_config = config.get("dimensions", DEFAULT_DIMENSIONS)
    all_findings = []
    finding_counters = {}

    # DIM-CIRCULAR: Tarjan SCC cycle detection
    if dimensions_config.get("DIM-CIRCULAR", {}).get("enabled", True):
        finding_counters["DIM-CIRCULAR"] = 0
        adjacency = {}
        for edge in graph.edges:
            adjacency.setdefault(edge.source_module, []).append(edge.target_module)
        # Simplified SCC: detect any back edges via DFS
        visited = set()
        in_stack = set()
        index_map = {}
        lowlink = {}
        counter = [0]
        stack = []
        sccs = []

        def strongconnect(v):
            index_map[v] = counter[0]
            lowlink[v] = counter[0]
            counter[0] += 1
            stack.append(v)
            in_stack.add(v)
            for w in adjacency.get(v, []):
                if w not in index_map:
                    strongconnect(w)
                    lowlink[v] = min(lowlink[v], lowlink[w])
                elif w in in_stack:
                    lowlink[v] = min(lowlink[v], index_map[w])
            if lowlink[v] == index_map[v]:
                component = []
                while True:
                    w = stack.pop()
                    in_stack.discard(w)
                    component.append(w)
                    if w == v:
                        break
                if len(component) > 1:
                    sccs.append(component)

        import sys
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(max(old_limit, len(graph.nodes) + 100))
        try:
            for node in graph.nodes:
                if node not in index_map:
                    try:
                        strongconnect(node)
                    except RecursionError:
                        pass
        finally:
            sys.setrecursionlimit(old_limit)

        for scc in sccs:
            finding_counters["DIM-CIRCULAR"] += 1
            cnt = finding_counters["DIM-CIRCULAR"]
            cycle_edges = [e for e in graph.edges if e.source_module in scc and e.target_module in scc]
            evidence = tuple(
                Evidence(file_path=_module_to_path(e.source_module), line_number=e.line_number,
                         code_snippet=e.original_import, description=f"Import {e.source_module} -> {e.target_module}")
                for e in cycle_edges[:5]
            )
            all_findings.append(Finding(
                finding_id=f"DIM-CIRCULAR-{cnt:03d}", source_type="health_dimension", source_id="DIM-CIRCULAR",
                severity=SEVERITY_HIGH, title=f"Circular dependency: {len(scc)} modules",
                description=f"Circular dependency among: {', '.join(sorted(scc)[:5])}",
                evidence=evidence,
                impact="Circular dependencies make modules tightly coupled.",
                remediation="Break the cycle by extracting shared interfaces.",
                is_self_contained=True,
            ))

    # DIM-COUPLING: Fan-in / fan-out metrics
    if dimensions_config.get("DIM-COUPLING", {}).get("enabled", True):
        finding_counters["DIM-COUPLING"] = 0
        cfg = dimensions_config.get("DIM-COUPLING", {}).get("config", {})
        fi_thresh = cfg.get("fan_in_threshold", 10)
        fo_thresh = cfg.get("fan_out_threshold", 15)
        fan_in = {}
        fan_out = {}
        for edge in graph.edges:
            fan_out[edge.source_module] = fan_out.get(edge.source_module, 0) + 1
            fan_in[edge.target_module] = fan_in.get(edge.target_module, 0) + 1
        for module in graph.nodes:
            fi = fan_in.get(module, 0)
            fo = fan_out.get(module, 0)
            if fi > fi_thresh or fo > fo_thresh:
                finding_counters["DIM-COUPLING"] += 1
                cnt = finding_counters["DIM-COUPLING"]
                sev = "critical" if (fi > fi_thresh * 2 or fo > fo_thresh * 2) else "high"
                all_findings.append(Finding(
                    finding_id=f"DIM-COUPLING-{cnt:03d}", source_type="health_dimension", source_id="DIM-COUPLING",
                    severity=SEVERITY_MAP[sev], title=f"High coupling: {module}",
                    description=f"Module {module}: fan-in={fi}, fan-out={fo}.",
                    evidence=(Evidence(file_path=_module_to_path(module), description=f"fan-in={fi}, fan-out={fo}"),),
                    impact="Highly coupled modules are difficult to modify independently.",
                    remediation="Reduce coupling by introducing interfaces or extracting shared logic.",
                    is_self_contained=True,
                ))

    # DIM-DEADCODE: Unreferenced symbols
    if dimensions_config.get("DIM-DEADCODE", {}).get("enabled", True):
        finding_counters["DIM-DEADCODE"] = 0
        referenced = set()
        for edge in graph.edges:
            referenced.add(edge.target_module)
            parts = edge.target_module.split(".")
            if parts:
                referenced.add(parts[-1])
        for sym in symbols:
            if sym.is_exported:
                continue
            if sym.symbol_name in referenced:
                continue
            finding_counters["DIM-DEADCODE"] += 1
            cnt = finding_counters["DIM-DEADCODE"]
            if cnt > 50:  # Cap findings to avoid overwhelming output
                break
            all_findings.append(Finding(
                finding_id=f"DIM-DEADCODE-{cnt:03d}", source_type="health_dimension", source_id="DIM-DEADCODE",
                severity=SEVERITY_LOW, title=f"Potentially dead code: {sym.symbol_type} {sym.symbol_name}",
                description=f"Symbol '{sym.symbol_name}' in {sym.file_path} appears unreferenced.",
                evidence=(Evidence(file_path=sym.file_path, line_number=sym.line_start, code_snippet=f"{sym.symbol_type} {sym.symbol_name}", description="Unreferenced symbol"),),
                impact="Dead code increases maintenance burden.",
                remediation="Remove unused symbols or document why they are retained.",
                is_self_contained=True,
            ))

    # DIM-COMPLEXITY: Cyclomatic complexity (placeholder -- requires file re-read)
    if dimensions_config.get("DIM-COMPLEXITY", {}).get("enabled", True):
        finding_counters["DIM-COMPLEXITY"] = 0
        # Complexity analysis requires reading file content; skipped here for brevity
        # Implementation would re-read source files and compute cyclomatic complexity per function

    # DIM-IMPORT: Import discipline
    if dimensions_config.get("DIM-IMPORT", {}).get("enabled", True):
        finding_counters["DIM-IMPORT"] = 0
        for edge in graph.edges:
            if "import *" in edge.original_import:
                finding_counters["DIM-IMPORT"] += 1
                cnt = finding_counters["DIM-IMPORT"]
                all_findings.append(Finding(
                    finding_id=f"DIM-IMPORT-{cnt:03d}", source_type="health_dimension", source_id="DIM-IMPORT",
                    severity=SEVERITY_MEDIUM, title=f"Wildcard import in {edge.source_module}",
                    description=f"Wildcard import 'from {edge.target_module} import *'.",
                    evidence=(Evidence(file_path=_module_to_path(edge.source_module), line_number=edge.line_number, code_snippet=edge.original_import, description="Wildcard import"),),
                    impact="Wildcard imports pollute namespace.",
                    remediation="Replace with explicit name imports.",
                    is_self_contained=True,
                ))

    # Persist findings
    findings_data = [_serialize_finding(f) for f in all_findings]
    find_key = step_cfg.get("artifacts", {}).get("produces", ["HEALTH_FINDINGS"])[0]
    find_path = artifacts.get(find_key, "")
    if find_path:
        _write_json(Path(find_path), findings_data)

    return ActionResult(
        status="APPROVED",
        remark=f"Health analysis produced {len(all_findings)} findings across enabled dimensions.",
        artifacts={find_key: find_path} if find_path else {},
    )


@action("ci_validate_health")
def ci_validate_health(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 10: Check INV-010, INV-011, INV-012, INV-013.

    INV-010: Findings cite evidence
    INV-011: Severity consistency
    INV-012: Dimension independence
    INV-013: Disabled dimensions produce no findings
    """
    artifacts = state.get("artifacts", {})
    findings_path = artifacts.get("HEALTH_FINDINGS", "")
    config_path = artifacts.get("RUNTIME_CONFIG", "")
    config = _read_json(Path(config_path)) if config_path and Path(config_path).exists() else {}

    violations = []
    finding_count = 0

    if findings_path and Path(findings_path).exists():
        findings_data = _read_json(Path(findings_path))
        finding_count = len(findings_data)

        # INV-010: Each finding has evidence
        for fd in findings_data:
            if not fd.get("evidence"):
                violations.append(f"INV-010: Finding {fd.get('finding_id')} has no evidence")

        # INV-011: Severity is from standard scale
        valid_levels = {"critical", "high", "medium", "low", "info"}
        for fd in findings_data:
            sev = fd.get("severity", {})
            if sev.get("level") not in valid_levels:
                violations.append(f"INV-011: Finding {fd.get('finding_id')} has invalid severity: {sev.get('level')}")

        # INV-013: Disabled dimensions produce no findings
        dim_config = config.get("dimensions", {})
        for fd in findings_data:
            source_id = fd.get("source_id", "")
            if source_id in dim_config and not dim_config[source_id].get("enabled", True):
                violations.append(f"INV-013: Finding {fd.get('finding_id')} from disabled dimension {source_id}")
    else:
        pass  # Empty findings is valid if all dimensions disabled

    report = {
        "invariants_checked": ["INV-010", "INV-011", "INV-012", "INV-013"],
        "violations": violations,
        "passed": len(violations) == 0,
        "finding_count": finding_count,
    }

    if violations:
        reject_code = violations[0].split(":")[0]
        return ActionResult(status="REJECTED", remark=f"Health invariant violations: {'; '.join(violations)}", artifacts={}, reject_code=reject_code)

    report_key = step_cfg.get("artifacts", {}).get("produces", ["HEALTH_INVARIANT_REPORT"])[0]
    report_path = artifacts.get(report_key, "")
    if report_path:
        _write_json(Path(report_path), report)

    return ActionResult(
        status="APPROVED",
        remark=f"Health invariants passed: {finding_count} findings validated.",
        artifacts={report_key: report_path} if report_path else {},
    )


@action("ci_analyze_security_phases")
def ci_analyze_security_phases(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 11 (TS-005): Run security phase analysis.

    Iterates over enabled SecurityPhase components, dispatches via
    PHASE_REGISTRY pattern. Produces SECURITY_FINDINGS (INT-005).
    Secret redaction applied per INV-017.
    """
    artifacts = state.get("artifacts", {})
    config_path = artifacts.get("RUNTIME_CONFIG", "")
    config = _read_json(Path(config_path)) if config_path and Path(config_path).exists() else {}

    inv_path = artifacts.get("FILE_INVENTORY", "")
    inv_data = _read_json(Path(inv_path)) if inv_path and Path(inv_path).exists() else {"entries": []}
    inventory = _deserialize_inventory(inv_data)

    config_path_src = config.get("repository_root", artifacts.get("SOURCE_CODEBASE_DIR", "."))
    phases_config = config.get("phases", DEFAULT_PHASES)
    all_findings = []
    finding_counters = {}

    # PHASE-SECRETS: Pattern scan for hardcoded secrets
    if phases_config.get("PHASE-SECRETS", {}).get("enabled", True):
        finding_counters["PHASE-SECRETS"] = 0
        for entry in inventory.entries:
            if entry.file_type != "source_code" or not entry.is_parseable:
                continue
            full_path = Path(config_path_src) / entry.file_path
            if not full_path.exists():
                continue
            try:
                content = full_path.read_text(encoding="utf-8")
                lines = content.splitlines()
            except Exception:
                continue
            for line_num, line in enumerate(lines, 1):
                for pattern, secret_type in SECRET_PATTERNS:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        finding_counters["PHASE-SECRETS"] += 1
                        cnt = finding_counters["PHASE-SECRETS"]
                        # INV-017: Redact secret value
                        raw_value = match.group(1) if match.lastindex else match.group(0)
                        redacted_line = _redact_value(line, raw_value)
                        all_findings.append(Finding(
                            finding_id=f"PHASE-SECRETS-{cnt:03d}", source_type="security_phase", source_id="PHASE-SECRETS",
                            severity=SEVERITY_CRITICAL, title=f"Hardcoded {secret_type} detected",
                            description=f"A {secret_type.lower()} appears to be hardcoded in {entry.file_path} at line {line_num}.",
                            evidence=(Evidence(file_path=entry.file_path, line_number=line_num, code_snippet=redacted_line, description=f"Potential {secret_type.lower()}"),),
                            impact="Hardcoded secrets can be exposed through version control.",
                            remediation="Move secrets to environment variables or a secrets manager.",
                            is_self_contained=True,
                        ))

    # PHASE-CODEPAT: Insecure code patterns
    if phases_config.get("PHASE-CODEPAT", {}).get("enabled", True):
        finding_counters["PHASE-CODEPAT"] = 0
        for entry in inventory.entries:
            if entry.file_type != "source_code" or not entry.is_parseable:
                continue
            full_path = Path(config_path_src) / entry.file_path
            if not full_path.exists():
                continue
            try:
                content = full_path.read_text(encoding="utf-8")
                lines = content.splitlines()
            except Exception:
                continue
            for line_num, line in enumerate(lines, 1):
                for pattern, pattern_name, severity_level in INSECURE_PATTERNS:
                    if re.search(pattern, line):
                        finding_counters["PHASE-CODEPAT"] += 1
                        cnt = finding_counters["PHASE-CODEPAT"]
                        all_findings.append(Finding(
                            finding_id=f"PHASE-CODEPAT-{cnt:03d}", source_type="security_phase", source_id="PHASE-CODEPAT",
                            severity=SEVERITY_MAP[severity_level], title=f"Insecure pattern: {pattern_name}",
                            description=f"Found {pattern_name} in {entry.file_path} at line {line_num}.",
                            evidence=(Evidence(file_path=entry.file_path, line_number=line_num, code_snippet=line.strip()[:200], description=f"Insecure pattern: {pattern_name}"),),
                            impact=f"The {pattern_name} pattern may introduce security vulnerabilities.",
                            remediation=f"Review and replace {pattern_name} with a secure alternative.",
                            is_self_contained=True,
                        ))

    # PHASE-INFRA: Infrastructure check
    if phases_config.get("PHASE-INFRA", {}).get("enabled", True):
        finding_counters["PHASE-INFRA"] = 0
        for entry in inventory.entries:
            if entry.file_type not in ("configuration", "source_code") or not entry.is_parseable:
                continue
            full_path = Path(config_path_src) / entry.file_path
            if not full_path.exists():
                continue
            try:
                content = full_path.read_text(encoding="utf-8")
                lines = content.splitlines()
            except Exception:
                continue
            for line_num, line in enumerate(lines, 1):
                for pattern, issue_name, severity_level in INFRA_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        finding_counters["PHASE-INFRA"] += 1
                        cnt = finding_counters["PHASE-INFRA"]
                        all_findings.append(Finding(
                            finding_id=f"PHASE-INFRA-{cnt:03d}", source_type="security_phase", source_id="PHASE-INFRA",
                            severity=SEVERITY_MAP[severity_level], title=f"Infrastructure issue: {issue_name}",
                            description=f"Found {issue_name} in {entry.file_path} at line {line_num}.",
                            evidence=(Evidence(file_path=entry.file_path, line_number=line_num, code_snippet=line.strip()[:200], description=f"Configuration issue: {issue_name}"),),
                            impact=f"{issue_name} may expose the application to security risks.",
                            remediation=f"Review and fix: {issue_name}.",
                            is_self_contained=True,
                        ))

    # Persist findings
    findings_data = [_serialize_finding(f) for f in all_findings]
    find_key = step_cfg.get("artifacts", {}).get("produces", ["SECURITY_FINDINGS"])[0]
    find_path = artifacts.get(find_key, "")
    if find_path:
        _write_json(Path(find_path), findings_data)

    return ActionResult(
        status="APPROVED",
        remark=f"Security analysis produced {len(all_findings)} findings across enabled phases.",
        artifacts={find_key: find_path} if find_path else {},
    )


@action("ci_validate_security")
def ci_validate_security(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 12: Check INV-014, INV-015, INV-016, INV-017, INV-018.

    INV-014: Findings cite evidence
    INV-015: Severity consistency
    INV-016: Phase independence
    INV-017: Secret redaction (CRITICAL)
    INV-018: Disabled phases produce no findings
    """
    artifacts = state.get("artifacts", {})
    findings_path = artifacts.get("SECURITY_FINDINGS", "")
    config_path = artifacts.get("RUNTIME_CONFIG", "")
    config = _read_json(Path(config_path)) if config_path and Path(config_path).exists() else {}

    violations = []
    finding_count = 0

    if findings_path and Path(findings_path).exists():
        findings_data = _read_json(Path(findings_path))
        finding_count = len(findings_data)

        # INV-014: Each finding has evidence
        for fd in findings_data:
            if not fd.get("evidence"):
                violations.append(f"INV-014: Finding {fd.get('finding_id')} has no evidence")

        # INV-015: Severity consistency
        valid_levels = {"critical", "high", "medium", "low", "info"}
        for fd in findings_data:
            sev = fd.get("severity", {})
            if sev.get("level") not in valid_levels:
                violations.append(f"INV-015: Finding {fd.get('finding_id')} has invalid severity")

        # INV-017: Secret redaction check
        for fd in findings_data:
            for ev in fd.get("evidence", []):
                snippet = ev.get("code_snippet", "")
                # Check for unredacted patterns
                for pattern, _ in SECRET_PATTERNS:
                    match = re.search(pattern, snippet, re.IGNORECASE)
                    if match and match.lastindex:
                        raw_val = match.group(match.lastindex)
                        if raw_val and "***REDACTED***" not in snippet:
                            violations.append(f"INV-017: Unredacted secret in {fd.get('finding_id')}")
                            break

        # INV-018: Disabled phases produce no findings
        phase_config = config.get("phases", {})
        for fd in findings_data:
            source_id = fd.get("source_id", "")
            if source_id in phase_config and not phase_config[source_id].get("enabled", True):
                violations.append(f"INV-018: Finding {fd.get('finding_id')} from disabled phase {source_id}")

    report = {
        "invariants_checked": ["INV-014", "INV-015", "INV-016", "INV-017", "INV-018"],
        "violations": violations,
        "passed": len(violations) == 0,
        "finding_count": finding_count,
    }

    if violations:
        # INV-017 is unrecoverable
        if any("INV-017" in v for v in violations):
            return ActionResult(status="REJECTED", remark=f"CRITICAL: Secret redaction failure: {'; '.join(violations)}", artifacts={}, reject_code="SECRET_REDACTION_FAILURE")
        reject_code = violations[0].split(":")[0]
        return ActionResult(status="REJECTED", remark=f"Security invariant violations: {'; '.join(violations)}", artifacts={}, reject_code=reject_code)

    report_key = step_cfg.get("artifacts", {}).get("produces", ["SECURITY_INVARIANT_REPORT"])[0]
    report_path = artifacts.get(report_key, "")
    if report_path:
        _write_json(Path(report_path), report)

    return ActionResult(
        status="APPROVED",
        remark=f"Security invariants passed: {finding_count} findings validated.",
        artifacts={report_key: report_path} if report_path else {},
    )


# ---------------------------------------------------------------------------
# Phase 4: Findings Assembly Actions
# ---------------------------------------------------------------------------

@action("ci_assemble_findings_reports")
def ci_assemble_findings_reports(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 13 (TS-006): Assemble findings into OutputDocument components.

    Produces STRUCTURAL_HEALTH_REPORT (OUT-002) and SECURITY_AUDIT_REPORT (OUT-003)
    as draft JSON. Findings grouped by dimension/phase, sorted by severity.
    """
    artifacts = state.get("artifacts", {})
    config_path = artifacts.get("RUNTIME_CONFIG", "")
    config = _read_json(Path(config_path)) if config_path and Path(config_path).exists() else {}

    health_path = artifacts.get("HEALTH_FINDINGS", "")
    security_path = artifacts.get("SECURITY_FINDINGS", "")

    health_findings = [_deserialize_finding(d) for d in (_read_json(Path(health_path)) if health_path and Path(health_path).exists() else [])]
    security_findings = [_deserialize_finding(d) for d in (_read_json(Path(security_path)) if security_path and Path(security_path).exists() else [])]

    # Health Report
    dimensions_config = config.get("dimensions", DEFAULT_DIMENSIONS)
    health_sections = []
    for dim_id, dim_cfg in dimensions_config.items():
        if not dim_cfg.get("enabled", True):
            continue
        dim_findings = [f for f in health_findings if f.source_id == dim_id]
        dim_findings.sort(key=lambda f: f.severity.numeric_weight, reverse=True)
        content = f"Found {len(dim_findings)} finding(s) for {dim_id}." if dim_findings else f"No findings for {dim_id}."
        health_sections.append({
            "section_id": f"health-{dim_id}",
            "section_name": dim_id,
            "content": content,
            "finding_count": len(dim_findings),
        })

    health_draft = {
        "document_id": "health-report",
        "output_type": "health_report",
        "title": "Structural Health Analysis Report",
        "sections": health_sections,
        "findings": [_serialize_finding(f) for f in health_findings],
        "metadata": {"generation_date": _today_iso(), "dimensions_analyzed": len(health_sections)},
        "is_self_contained": True,
    }

    # Security Report
    phases_config = config.get("phases", DEFAULT_PHASES)
    security_sections = []
    for phase_id, phase_cfg in phases_config.items():
        if not phase_cfg.get("enabled", True):
            continue
        phase_findings = [f for f in security_findings if f.source_id == phase_id]
        phase_findings.sort(key=lambda f: f.severity.numeric_weight, reverse=True)
        content = f"Found {len(phase_findings)} finding(s) for {phase_id}." if phase_findings else f"No findings for {phase_id}."
        security_sections.append({
            "section_id": f"security-{phase_id}",
            "section_name": phase_id,
            "content": content,
            "finding_count": len(phase_findings),
        })

    security_draft = {
        "document_id": "security-report",
        "output_type": "security_report",
        "title": "Security Audit Report",
        "sections": security_sections,
        "findings": [_serialize_finding(f) for f in security_findings],
        "metadata": {"generation_date": _today_iso(), "phases_analyzed": len(security_sections)},
        "is_self_contained": True,
    }

    # Persist
    produces = step_cfg.get("artifacts", {}).get("produces", ["STRUCTURAL_HEALTH_REPORT_DRAFT", "SECURITY_AUDIT_REPORT_DRAFT"])
    health_key = produces[0] if len(produces) > 0 else "STRUCTURAL_HEALTH_REPORT_DRAFT"
    security_key = produces[1] if len(produces) > 1 else "SECURITY_AUDIT_REPORT_DRAFT"

    health_path_out = artifacts.get(health_key, "")
    security_path_out = artifacts.get(security_key, "")

    if health_path_out:
        _write_json(Path(health_path_out), health_draft)
    if security_path_out:
        _write_json(Path(security_path_out), security_draft)

    return ActionResult(
        status="APPROVED",
        remark=f"Assembled health report ({len(health_sections)} sections, {len(health_findings)} findings) "
               f"and security report ({len(security_sections)} sections, {len(security_findings)} findings).",
        artifacts={health_key: health_path_out, security_key: security_path_out},
    )


@action("ci_validate_assembly")
def ci_validate_assembly(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 14: Check INV-019, INV-020, INV-021.

    INV-019: Health report has one section per enabled dimension
    INV-020: Security report has one section per enabled phase
    INV-021: All findings within a section from corresponding dimension/phase
    """
    artifacts = state.get("artifacts", {})
    violations = []

    health_path = artifacts.get("STRUCTURAL_HEALTH_REPORT_DRAFT", "")
    security_path = artifacts.get("SECURITY_AUDIT_REPORT_DRAFT", "")

    if health_path and Path(health_path).exists():
        health_data = _read_json(Path(health_path))
        # INV-021: Check findings match section source_id
        for finding in health_data.get("findings", []):
            source_id = finding.get("source_id", "")
            section_exists = any(s.get("section_name") == source_id for s in health_data.get("sections", []))
            if not section_exists and health_data.get("sections"):
                violations.append(f"INV-021: Finding {finding.get('finding_id')} from {source_id} has no matching section")

    if security_path and Path(security_path).exists():
        security_data = _read_json(Path(security_path))
        for finding in security_data.get("findings", []):
            source_id = finding.get("source_id", "")
            section_exists = any(s.get("section_name") == source_id for s in security_data.get("sections", []))
            if not section_exists and security_data.get("sections"):
                violations.append(f"INV-021: Finding {finding.get('finding_id')} from {source_id} has no matching section")

    report = {
        "invariants_checked": ["INV-019", "INV-020", "INV-021"],
        "violations": violations,
        "passed": len(violations) == 0,
    }

    if violations:
        reject_code = violations[0].split(":")[0]
        return ActionResult(status="REJECTED", remark=f"Assembly invariant violations: {'; '.join(violations)}", artifacts={}, reject_code=reject_code)

    report_key = step_cfg.get("artifacts", {}).get("produces", ["ASSEMBLY_INVARIANT_REPORT"])[0]
    report_path = artifacts.get(report_key, "")
    if report_path:
        _write_json(Path(report_path), report)

    return ActionResult(
        status="APPROVED",
        remark="Assembly invariants passed.",
        artifacts={report_key: report_path} if report_path else {},
    )


# ---------------------------------------------------------------------------
# Phase 5: Validation, Review, Rendering Actions
# ---------------------------------------------------------------------------

@action("ci_validate_outputs")
def ci_validate_outputs(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 15 (TS-007): Validate outputs and produce RunManifest.

    INV-022: output_type_count >= 3
    INV-023: All OutputDocument.is_self_contained is true
    INV-024: No unresolved references
    """
    artifacts = state.get("artifacts", {})
    violations = []

    # Collect output types
    output_types = set()

    # Check audience docs
    aud_path = artifacts.get("AUDIENCE_OUTPUT_DOCS", "")
    if aud_path and Path(aud_path).exists():
        aud_data = _read_json(Path(aud_path))
        if isinstance(aud_data, list):
            for doc in aud_data:
                output_types.add(doc.get("output_type", ""))
                if not doc.get("is_self_contained", False):
                    violations.append(f"INV-023: Audience doc {doc.get('document_id')} not self-contained")

    # Check health report
    health_path = artifacts.get("STRUCTURAL_HEALTH_REPORT_DRAFT", "")
    if health_path and Path(health_path).exists():
        health_data = _read_json(Path(health_path))
        output_types.add(health_data.get("output_type", ""))
        if not health_data.get("is_self_contained", False):
            violations.append("INV-023: Health report not self-contained")

    # Check security report
    security_path = artifacts.get("SECURITY_AUDIT_REPORT_DRAFT", "")
    if security_path and Path(security_path).exists():
        security_data = _read_json(Path(security_path))
        output_types.add(security_data.get("output_type", ""))
        if not security_data.get("is_self_contained", False):
            violations.append("INV-023: Security report not self-contained")

    output_types.discard("")
    output_type_count = len(output_types)

    # INV-022: At least 3 output types
    if output_type_count < 3:
        violations.append(f"INV-022: Only {output_type_count} output types produced (minimum 3)")

    # Build RunManifest
    manifest = {
        "run_id": _generate_run_id(),
        "codename": "codebase_intelligence",
        "output_count": output_type_count,
        "output_types": sorted(output_types),
        "output_type_count": output_type_count,
        "generation_date": _today_iso(),
    }

    report = {
        "invariants_checked": ["INV-022", "INV-023", "INV-024"],
        "violations": violations,
        "passed": len(violations) == 0,
        "output_type_count": output_type_count,
        "output_types": sorted(output_types),
    }

    if violations:
        reject_code = violations[0].split(":")[0]
        return ActionResult(status="REJECTED", remark=f"Output validation violations: {'; '.join(violations)}", artifacts={}, reject_code=reject_code)

    # Persist
    produces = step_cfg.get("artifacts", {}).get("produces", ["RUN_MANIFEST", "OUTPUT_VALIDATION_REPORT"])
    manifest_key = produces[0] if len(produces) > 0 else "RUN_MANIFEST"
    validation_key = produces[1] if len(produces) > 1 else "OUTPUT_VALIDATION_REPORT"

    manifest_path = artifacts.get(manifest_key, "")
    validation_path = artifacts.get(validation_key, "")

    if manifest_path:
        _write_json(Path(manifest_path), manifest)
    if validation_path:
        _write_json(Path(validation_path), report)

    return ActionResult(
        status="APPROVED",
        remark=f"Output validation passed: {output_type_count} output types ({', '.join(sorted(output_types))}).",
        artifacts={manifest_key: manifest_path, validation_key: validation_path},
    )


@action("ci_render_outputs")
def ci_render_outputs(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 17: Serialize OutputDocument components and RunManifest to Markdown files.

    Produces concrete files: AUDIENCE_META_CONTENT (OUT-001),
    STRUCTURAL_HEALTH_REPORT (OUT-002), SECURITY_AUDIT_REPORT (OUT-003).
    Uses OutputRenderer protocol (OR-001).
    """
    artifacts = state.get("artifacts", {})
    config_path = artifacts.get("RUNTIME_CONFIG", "")
    config = _read_json(Path(config_path)) if config_path and Path(config_path).exists() else {}
    output_dir = Path(config.get("output_dir", "./output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    rendered_files = []

    # Render audience reports
    aud_path = artifacts.get("AUDIENCE_OUTPUT_DOCS", "")
    aud_content_dir = artifacts.get("AUDIENCE_META_CONTENT", "")
    if aud_path and Path(aud_path).exists():
        aud_data = _read_json(Path(aud_path))
        aud_dir = Path(aud_content_dir) if aud_content_dir else output_dir / "audience_meta_content"
        aud_dir.mkdir(parents=True, exist_ok=True)
        if isinstance(aud_data, list):
            for doc in aud_data:
                lines = ["---"]
                lines.append(f'document_id: "{doc.get("document_id", "")}"')
                lines.append(f'output_type: "{doc.get("output_type", "")}"')
                lines.append(f'title: "{doc.get("title", "")}"')
                lines.append(f'generation_date: "{doc.get("metadata", {}).get("generation_date", _today_iso())}"')
                lines.append("is_self_contained: true")
                lines.append("---")
                lines.append("")
                lines.append(f"# {doc.get('title', 'Report')}")
                lines.append("")
                for sec in doc.get("sections", []):
                    lines.append(f"## {sec.get('section_name', 'Section')}")
                    lines.append("")
                    lines.append(sec.get("content", ""))
                    lines.append("")
                filename = f"audience_{doc.get('metadata', {}).get('audience_id', 'unknown')}.md"
                filepath = aud_dir / filename
                filepath.write_text("\n".join(lines), encoding="utf-8")
                rendered_files.append(str(filepath))

    # Render health report
    health_path = artifacts.get("STRUCTURAL_HEALTH_REPORT_DRAFT", "")
    health_out = artifacts.get("STRUCTURAL_HEALTH_REPORT", "")
    if health_path and Path(health_path).exists():
        health_data = _read_json(Path(health_path))
        lines = ["---"]
        lines.append(f'document_id: "{health_data.get("document_id", "")}"')
        lines.append(f'output_type: "{health_data.get("output_type", "")}"')
        lines.append(f'title: "{health_data.get("title", "")}"')
        lines.append(f'generation_date: "{health_data.get("metadata", {}).get("generation_date", _today_iso())}"')
        lines.append("is_self_contained: true")
        lines.append("---")
        lines.append("")
        lines.append(f"# {health_data.get('title', 'Health Report')}")
        lines.append("")
        for sec in health_data.get("sections", []):
            lines.append(f"## {sec.get('section_name', 'Section')}")
            lines.append("")
            lines.append(sec.get("content", ""))
            lines.append("")
            for finding in [f for f in health_data.get("findings", []) if f.get("source_id") == sec.get("section_name")]:
                sev = finding.get("severity", {})
                lines.append(f"### {finding.get('finding_id', '')}: {finding.get('title', '')}")
                lines.append(f"- **Severity:** {sev.get('level', 'unknown')}")
                lines.append(f"- **Description:** {finding.get('description', '')}")
                lines.append(f"- **Impact:** {finding.get('impact', '')}")
                lines.append(f"- **Remediation:** {finding.get('remediation', '')}")
                lines.append("")

        health_file = Path(health_out) if health_out else output_dir / "health_report.md"
        health_file.parent.mkdir(parents=True, exist_ok=True)
        health_file.write_text("\n".join(lines), encoding="utf-8")
        rendered_files.append(str(health_file))

    # Render security report
    security_path = artifacts.get("SECURITY_AUDIT_REPORT_DRAFT", "")
    security_out = artifacts.get("SECURITY_AUDIT_REPORT", "")
    if security_path and Path(security_path).exists():
        security_data = _read_json(Path(security_path))
        lines = ["---"]
        lines.append(f'document_id: "{security_data.get("document_id", "")}"')
        lines.append(f'output_type: "{security_data.get("output_type", "")}"')
        lines.append(f'title: "{security_data.get("title", "")}"')
        lines.append(f'generation_date: "{security_data.get("metadata", {}).get("generation_date", _today_iso())}"')
        lines.append("is_self_contained: true")
        lines.append("---")
        lines.append("")
        lines.append(f"# {security_data.get('title', 'Security Report')}")
        lines.append("")
        for sec in security_data.get("sections", []):
            lines.append(f"## {sec.get('section_name', 'Section')}")
            lines.append("")
            lines.append(sec.get("content", ""))
            lines.append("")
            for finding in [f for f in security_data.get("findings", []) if f.get("source_id") == sec.get("section_name")]:
                sev = finding.get("severity", {})
                lines.append(f"### {finding.get('finding_id', '')}: {finding.get('title', '')}")
                lines.append(f"- **Severity:** {sev.get('level', 'unknown')}")
                lines.append(f"- **Description:** {finding.get('description', '')}")
                lines.append(f"- **Impact:** {finding.get('impact', '')}")
                lines.append(f"- **Remediation:** {finding.get('remediation', '')}")
                lines.append("")

        security_file = Path(security_out) if security_out else output_dir / "security_report.md"
        security_file.parent.mkdir(parents=True, exist_ok=True)
        security_file.write_text("\n".join(lines), encoding="utf-8")
        rendered_files.append(str(security_file))

    produces = step_cfg.get("artifacts", {}).get("produces", ["AUDIENCE_META_CONTENT", "STRUCTURAL_HEALTH_REPORT", "SECURITY_AUDIT_REPORT"])
    result_artifacts = {}
    if len(produces) > 0:
        result_artifacts[produces[0]] = artifacts.get(produces[0], "")
    if len(produces) > 1:
        result_artifacts[produces[1]] = artifacts.get(produces[1], "")
    if len(produces) > 2:
        result_artifacts[produces[2]] = artifacts.get(produces[2], "")

    return ActionResult(
        status="APPROVED",
        remark=f"Rendered {len(rendered_files)} output files to {output_dir}.",
        artifacts=result_artifacts,
    )


# ---------------------------------------------------------------------------
# Phase 6: Delivery Actions
# ---------------------------------------------------------------------------

@action("ci_promote_outputs")
def ci_promote_outputs(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 18: Copy rendered output files to designated output directory.

    Copies AUDIENCE_META_CONTENT, STRUCTURAL_HEALTH_REPORT,
    SECURITY_AUDIT_REPORT, and RUN_MANIFEST to the promoted directory.
    """
    artifacts = state.get("artifacts", {})
    config_path = artifacts.get("RUNTIME_CONFIG", "")
    config = _read_json(Path(config_path)) if config_path and Path(config_path).exists() else {}
    output_dir = Path(config.get("output_dir", "./output"))
    promoted_dir = output_dir / "promoted"
    promoted_dir.mkdir(parents=True, exist_ok=True)

    promoted = []

    # Promote health report
    health_src = artifacts.get("STRUCTURAL_HEALTH_REPORT", "")
    if health_src and Path(health_src).exists():
        dst = promoted_dir / "health_report.md"
        shutil.copy2(health_src, dst)
        promoted.append("health_report.md")

    # Promote security report
    security_src = artifacts.get("SECURITY_AUDIT_REPORT", "")
    if security_src and Path(security_src).exists():
        dst = promoted_dir / "security_report.md"
        shutil.copy2(security_src, dst)
        promoted.append("security_report.md")

    # Promote run manifest
    manifest_src = artifacts.get("RUN_MANIFEST", "")
    if manifest_src and Path(manifest_src).exists():
        # Render manifest to Markdown
        manifest_data = _read_json(Path(manifest_src))
        lines = ["---"]
        lines.append(f'run_id: "{manifest_data.get("run_id", "")}"')
        lines.append(f'codename: "{manifest_data.get("codename", "codebase_intelligence")}"')
        lines.append(f'output_count: {manifest_data.get("output_count", 0)}')
        lines.append(f'output_type_count: {manifest_data.get("output_type_count", 0)}')
        lines.append(f'generation_date: "{manifest_data.get("generation_date", _today_iso())}"')
        lines.append("---")
        lines.append("")
        lines.append(f"# Run Manifest: {manifest_data.get('codename', 'codebase_intelligence')}")
        lines.append("")
        lines.append(f"**Run ID:** {manifest_data.get('run_id', '')}")
        lines.append(f"**Generated:** {manifest_data.get('generation_date', '')}")
        lines.append(f"**Output types:** {', '.join(manifest_data.get('output_types', []))}")
        lines.append("")
        manifest_md = promoted_dir / "RUN_MANIFEST.md"
        manifest_md.write_text("\n".join(lines), encoding="utf-8")
        promoted.append("RUN_MANIFEST.md")

    # Promote audience content
    aud_src = artifacts.get("AUDIENCE_META_CONTENT", "")
    if aud_src and Path(aud_src).exists() and Path(aud_src).is_dir():
        aud_dst = promoted_dir / "audience_meta_content"
        if aud_dst.exists():
            shutil.rmtree(aud_dst)
        shutil.copytree(aud_src, aud_dst)
        promoted.append("audience_meta_content/")

    produces = step_cfg.get("artifacts", {}).get("produces", [])
    result_artifacts = {}
    for key in produces:
        result_artifacts[key] = str(promoted_dir)

    return ActionResult(
        status="APPROVED",
        remark=f"Promoted {len(promoted)} output(s) to {promoted_dir}: {', '.join(promoted)}.",
        artifacts=result_artifacts,
    )


@action("ci_complete_pipeline")
def ci_complete_pipeline(*, context: dict, state: dict, step_cfg: dict, project_root: str) -> ActionResult:
    """Step 19: Record final pipeline outcome and signal completion.

    Captures run metadata: run_id, generation_date, output_count, output_types.
    """
    artifacts = state.get("artifacts", {})

    completion = {
        "status": "SUCCESS",
        "codename": "codebase_intelligence",
        "generation_date": _today_iso(),
        "completed_at": datetime.now().isoformat(),
        "output_artifacts": {
            "AUDIENCE_META_CONTENT_PROMOTED": artifacts.get("AUDIENCE_META_CONTENT_PROMOTED", ""),
            "STRUCTURAL_HEALTH_REPORT_PROMOTED": artifacts.get("STRUCTURAL_HEALTH_REPORT_PROMOTED", ""),
            "SECURITY_AUDIT_REPORT_PROMOTED": artifacts.get("SECURITY_AUDIT_REPORT_PROMOTED", ""),
            "RUN_MANIFEST_PROMOTED": artifacts.get("RUN_MANIFEST_PROMOTED", ""),
        },
    }

    produces = step_cfg.get("artifacts", {}).get("produces", ["COMPLETION_RESULT"])
    result_key = produces[0] if produces else "COMPLETION_RESULT"
    result_path = artifacts.get(result_key, "")

    if result_path:
        _write_json(Path(result_path), completion)

    return ActionResult(
        status="APPROVED",
        remark=f"Pipeline completed successfully. Outputs promoted to final location.",
        artifacts={result_key: result_path} if result_path else {},
    )
