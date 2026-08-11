# Codebase Intelligence Generator

Generates multiple intelligence reports from codebase including audience-specific meta content, structural health analysis, and security audit findings.

**Version:** 1.0.0

## Pipeline Steps

| # | Step | Type | Detail |
|---|------|------|--------|
| 1 | scan_codebase | action | scan_codebase_files |
| 2 | build_import_graph | action | build_import_graph |
| 3 | generate_audience_meta | prompt | prompts/03_generate_audience_meta.txt |
| 4 | analyze_health | prompt | prompts/04_analyze_health.txt |
| 5 | analyze_security | prompt | prompts/05_analyze_security.txt |
| 6 | generate_findings_report | prompt | prompts/06_generate_findings_report.txt |
| 7 | validate_outputs | action | validate_intelligence_outputs |
| 8 | step_completion | action | step_completion |

## Implementations

| Name | Description |
|------|-------------|
| default | Default implementation (workflow.toml) |
| executive_summary | Produces high-level executive summaries with strategic recommendations instead of detailed technical findings |
| technical_deep_dive | Produces exhaustive technical analysis with code-level evidence, dependency graphs, and remediation code samples |
| security_focused | Prioritizes security and compliance analysis with expanded vulnerability scanning and audit-ready output |

## Usage

```bash
ukbe-run-agent run --template-group codebase_intelligence
```

## File Structure

```
codebase_intelligence/
    workflow.toml
    context_extensions.py
    actions.py
    prompts/
    impls/          (if alternative implementations exist)
    README.md
```
