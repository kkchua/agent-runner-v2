# Codebase Intelligence Generator

## Overview

The codebase_intelligence workflow scans a codebase of Rich Markdown
documentation and Python source code, performs structural health analysis
across 5 dimensions, security audit across 5 phases, and produces
audience-tailored intelligence reports.

**Codename:** codebase_intelligence

**Version:** 1.0.0

**Pattern:** Input Transformation (Pattern 2, per BASE_COMPOSITION_STANDARD_v1.0.md)

**Layers:** 3 (Input Parsing -> Analysis -> Output Rendering)

**Stages:** 7 (TS-001 through TS-007)

**Invariants:** 24 (INV-001 through INV-024)

**Steps:** 20 (18 action-driven, 2 prompt-driven)

---

## Input Artifacts

| Key | Type | Required | Description |
|---|---|---|---|
| SOURCE_CODEBASE_DIR | Directory | Yes | Target repository root containing codebase files to analyze |
| AUDIENCES_DIR | Directory | No | Directory containing audience definition .md files |
| CONFIG_FILE | File | No | JSON configuration for dimensions, phases, and rendering |

---

## Output Artifacts

| Key | Type | Description |
|---|---|---|
| AUDIENCE_META_CONTENT | Directory | Audience-tailored Markdown reports (one per audience) |
| STRUCTURAL_HEALTH_REPORT | File (Markdown) | Health dimension findings report |
| SECURITY_AUDIT_REPORT | File (Markdown) | Security phase findings report |
| RUN_MANIFEST | File (Markdown) | Run-level metadata and summary |

---

## Pipeline Architecture

The workflow follows a 7-stage transformation pipeline:

| Stage | Name | Description |
|---|---|---|
| TS-001 | Codebase Scan | Walk directory tree, classify files, build FileInventory |
| TS-002 | Import Graph Construction | AST-parse Python files, extract imports and symbols |
| TS-003 | Audience Analysis | Filter codebase by audience focus areas, generate reports |
| TS-004 | Health Dimension Analysis | Run 5 structural health dimensions |
| TS-005 | Security Phase Analysis | Run 5 security analysis phases |
| TS-006 | Findings Report Assembly | Group findings into health and security reports |
| TS-007 | Output Validation | Verify output constraints, produce RunManifest |

---

## Workflow Steps

### Phase 1: Input Preparation

| # | Step | Type | Description |
|---|---|---|---|
| 1 | validate_input | action | Check V-IN-001 to V-IN-004 constraints |
| 2 | prepare_configuration | action | Build RuntimeConfig from config file and defaults |

### Phase 2: Input Parsing (Layer 1)

| # | Step | Type | Description |
|---|---|---|---|
| 3 | scan_codebase | action | TS-001: Walk codebase, build FileInventory |
| 4 | validate_scan | action | Check INV-001, INV-002, INV-003 |
| 5 | build_import_graph | action | TS-002: AST-parse imports and symbols |
| 6 | validate_import_graph | action | Check INV-004, INV-005, INV-006 |

### Phase 3: Analysis (Layer 2)

| # | Step | Type | Description |
|---|---|---|---|
| 7 | analyze_audiences | action | TS-003: Generate audience reports |
| 8 | validate_audiences | action | Check INV-007 to INV-009, INV-012 |
| 9 | analyze_health_dimensions | action | TS-004: Run 5 health dimensions |
| 10 | validate_health | action | Check INV-010 to INV-013 |
| 11 | analyze_security_phases | action | TS-005: Run 5 security phases |
| 12 | validate_security | action | Check INV-014 to INV-018 |

### Phase 4: Findings Assembly

| # | Step | Type | Description |
|---|---|---|---|
| 13 | assemble_findings_reports | action | TS-006: Group findings into reports |
| 14 | validate_assembly | action | Check INV-019 to INV-021 |

### Phase 5: Validation and Review

| # | Step | Type | Description |
|---|---|---|---|
| 15 | validate_outputs | action | TS-007: Check INV-022 to INV-024 |
| 16 | review_quality | prompt | LLM quality review of findings |
| 17 | render_outputs | action | Serialize to Markdown files |

### Phase 6: Delivery

| # | Step | Type | Description |
|---|---|---|---|
| 18 | promote_outputs | action | Copy outputs to final location |
| 19 | complete_pipeline | action | Record completion metadata |

### Auxiliary (Refinement Only)

| # | Step | Type | Description |
|---|---|---|---|
| 20 | adjust_parameters | prompt | Modify thresholds on quality rejection |

---

## Health Dimensions

| ID | Name | Description |
|---|---|---|
| DIM-CIRCULAR | Circular Dependencies | Detect cycles via Tarjan SCC |
| DIM-COUPLING | Coupling Metrics | Fan-in / fan-out per module |
| DIM-DEADCODE | Dead Code | Unreferenced symbols |
| DIM-COMPLEXITY | Complexity | Cyclomatic complexity per function |
| DIM-IMPORT | Import Discipline | Anti-patterns (wildcard, private) |

---

## Security Phases

| ID | Name | Description |
|---|---|---|
| PHASE-SECRETS | Secrets Detection | Pattern scan for hardcoded secrets |
| PHASE-DEPS | Dependencies Audit | Known vulnerable dependencies |
| PHASE-CODEPAT | Code Patterns Scan | Insecure coding patterns |
| PHASE-AUTH | Authentication Review | Auth implementation issues |
| PHASE-INFRA | Infrastructure Check | Deployment/config security |

---

## Configuration

The workflow accepts a JSON configuration file with the following structure:

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
    "PHASE-DEPS": {"enabled": true, "config": {}},
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

Override precedence (highest to lowest):
1. Environment variables
2. Config file values
3. Built-in defaults

---

## Quality Review Loop

When review_quality (Step 16) determines that findings do not meet
quality standards, the workflow enters an adjustment loop:

1. review_quality evaluates evidence sufficiency, remediation clarity,
   finding prioritization, report completeness, and coherence.
2. If rejected, adjust_parameters modifies RuntimeConfig thresholds.
3. Analysis pipeline re-executes from Step 7 through Step 15.
4. Maximum 2 iterations before QUALITY_REVIEW_EXHAUSTED.

---

## Extension Points

| ID | Extension | How to Extend |
|---|---|---|
| EXT-001 | Custom Audiences | Drop .md file in audiences/ directory |
| EXT-002 | Custom Health Dimensions | Register in DIMENSION_REGISTRY |
| EXT-003 | Custom Security Phases | Register in PHASE_REGISTRY |
| EXT-004 | Configurable Thresholds | Modify config object |
| EXT-005 | Output Formats | Register in RENDERER_REGISTRY |
| EXT-006 | Incremental Analysis | Add cache layer to InputParser |

---

## File Structure

```
workflows/codebase_intelligence/
    standards/
        COMPOSITION_STANDARD.md
    impls/
        default.impl.md
    workflow.toml
    context_extensions.py
    actions.py
    prompts/
        review_quality.txt
        adjust_parameters.txt
    README.md
    Specs/
        codebase_intelligence.md
```

---

## Traceability

All content traces to:
- REQUIREMENT_ANALYSIS-01.md (generator requirements)
- COMPOSITION_SPEC-01.md (transformation contract)
- RUNTIME_IMPL-01.md (runtime implementation design)
- ARTIFACT_CONTRACT-01.md (artifact definitions)
- STEP_SEQUENCE-01.md (step definitions)
- BASE_COMPOSITION_STANDARD_v1.0.md (governance standard)

---

**End of README**
